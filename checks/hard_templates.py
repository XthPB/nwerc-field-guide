"""Compile the four published C++17 template excerpts and compare their public operations to direct models."""
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess


class Code(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "code" and dict(attrs).get("class") == "language-cpp":
            self.active = True

    def handle_endtag(self, tag):
        if tag == "code":
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)


TEST = r"""
#include <algorithm>
#include <cassert>
#include <climits>
#include <functional>
#include <iostream>
#include <limits>
#include <numeric>
#include <optional>
#include <random>
#include <utility>
#include <vector>
PUBLIC_TEMPLATES

int main() {
    std::mt19937 rng(40717);
    int checks = 0;
    std::vector<long long> values(23,LLONG_MIN);
    FirstAbove maxTree((int)values.size());
    for (int step = 0; step < 120; ++step) {
        int i = rng()%values.size();
        values[i] = step%7 == 0 ? LLONG_MIN : (int)(rng()%13)-6;
        maxTree.set(i,values[i]);
        for (int start = 0; start <= (int)values.size(); ++start) {
            for (long long threshold : {LLONG_MIN,-2LL,1LL,LLONG_MAX}) {
                int target = -1;
                for (int j=start; j<(int)values.size(); ++j) {
                    if (values[j]>threshold) { target=j; break; }
                }
                assert(maxTree.first(start,threshold)==target);
                ++checks;
            }
        }
    }

    FenwickGrid grid(5,6);
    long long cells[5][6] = {};
    for (int step = 0; step < 32; ++step) {
        int i=rng()%5, j=rng()%6, delta=(int)(rng()%9)-4;
        grid.add(i,j,delta);
        cells[i][j] += delta;
        for (int top=0; top<=5; ++top) for (int bottom=top; bottom<=5; ++bottom)
        for (int left=0; left<=6; ++left) for (int right=left; right<=6; ++right) {
            long long target=0;
            for (int r=top;r<bottom;++r) for(int c=left;c<right;++c) target+=cells[r][c];
            assert(grid.sum(top,left,bottom,right)==target);
            ++checks;
        }
    }

    for (int width: {1,2,6,64}) {
        std::vector<int> a(27,1);
        ForwardJumps jumps(a,width);
        for (int step=0; step<80; ++step) {
            int i=rng()%a.size();
            a[i]=step%5==0 ? INT_MAX : (int)(rng()%8)+1;
            jumps.set(i,a[i]);
            for(int start=0;start<(int)a.size();++start) {
                int last=start, count=0;
                for(long long pos=start;pos<(int)a.size();pos+=a[pos]) {
                    last=(int)pos; ++count;
                }
                assert(jumps.query(start)==std::make_pair(last,count));
                ++checks;
            }
        }
    }

    using Word=unsigned long long;
    using Tree=std::vector<std::vector<std::pair<int,Word>>>;
    UndoXorForest forest(7);
    auto from=[&](const Tree& t,int u) {
        std::vector<std::optional<Word>> d(t.size());
        std::vector<int> queue{u};
        d[u]=0;
        for (int at=0; at<(int)queue.size(); ++at) {
            int v=queue[at];
            for (auto [w,label]:t[v]) if (!d[w]) {
                d[w]=*d[v]^label;queue.push_back(w);
            }
        }
        return d;
    };
    auto compare=[&](const Tree& t) {
        for (int u=0;u<(int)t.size();++u) {
            auto d=from(t,u);
            auto a=forest.find(u);
            for(int v=0;v<(int)t.size();++v) {
                auto b=forest.find(v);
                assert(d[v].has_value()==(a.first==b.first));
                if (d[v]) assert(*d[v]==(a.second^b.second));
                ++checks;
            }
        }
    };
    std::function<void(Tree,int)> visit=[&](Tree current,int depth) {
        int mark=forest.checkpoint();
        Tree before=current;
        for(int i=0;i<4;++i) {
            int u=rng()%7,v=rng()%7;Word w=rng()%16;
            auto prior=from(current,u)[v];
            auto cycle=forest.add(u,v,w);
            if(prior) assert(cycle && *cycle==(*prior^w));
            else {
                assert(!cycle);
                current[u].emplace_back(v,w);current[v].emplace_back(u,w);
            }
            ++checks;compare(current);
        }
        if(depth<3) {visit(current,depth+1);visit(current,depth+1);}
        forest.rollback(mark);compare(before);
    };
    visit(Tree(7),0);
    std::cout<<checks<<" template checks passed\n";
}
"""


def main():
    root = Path(__file__).resolve().parents[1]
    programs = []
    for key in ["max-search", "fenwick-grid", "jump-block-table", "undo-xor"]:
        code = Code()
        code.feed((root / "templates" / (key + ".html")).read_text())
        assert code.parts, key
        programs.append("".join(code.parts))
    with TemporaryDirectory() as temp:
        source = Path(temp) / "check.cpp"
        executable = Path(temp) / "check"
        source.write_text(TEST.replace("PUBLIC_TEMPLATES", "\n".join(programs)))
        subprocess.run([os.environ.get("CXX", "c++"), "-std=c++17", "-Wall", "-Wextra", "-O2", str(source), "-o", str(executable)], check=True)
        subprocess.run([str(executable)], check=True)


if __name__ == "__main__":
    main()
